import {Composition} from 'remotion';
import {VerticalStarter, verticalVideoSchema} from './VerticalStarter';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="VerticalStarter"
        component={VerticalStarter}
        durationInFrames={300}
        fps={30}
        width={1080}
        height={1920}
        schema={verticalVideoSchema}
        defaultProps={{
          title: 'Road Safety Quick Tip',
          subtitle: 'Keep 7+ seconds following distance in rain',
          accentColor: '#22d3ee',
        }}
      />
    </>
  );
};
